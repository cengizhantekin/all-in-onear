import copy
import json
import unittest
from unittest.mock import MagicMock, patch
from experiments import quotes
from experiments.common import QUOTE_URL, NoQuoteRedirect, fetch_json, quote_preview


def fixture():
    deadline = '2026-11-10T15:00:00Z'
    cells = []
    for origin, destination in quotes.ROUTES:
        for amount in quotes.AMOUNTS:
            request = quotes.request_for(origin, destination, amount, deadline)
            out = str(amount * 10**6 - 100000)
            cells.append({'origin': origin, 'destination': destination, 'input_usdc': amount,
                'observation': {'endpoint': QUOTE_URL, 'request': request, 'http_status': 201,
                    'response_ms': 123, 'response': {'quoteRequest': copy.deepcopy(request),
                        'quote': {'amountIn': request['amount'], 'amountOut': out,
                                  'minAmountOut': str(int(out) * 99 // 100), 'timeEstimate': 32}}}})
    return {'policy': copy.deepcopy(quotes.POLICY), 'deadline': deadline, 'cells': cells}


class QuoteTests(unittest.TestCase):
    def test_failed_cells_remain_in_the_planned_denominator(self):
        evidence = fixture()
        evidence['cells'][0]['observation'].update(http_status=400, response={'message': 'No route'})
        evidence['cells'][1]['observation'].update(http_status=None, transport_error='TimeoutError')
        result = quotes.analyze(evidence)
        self.assertEqual(result['quoted'], 4)
        self.assertEqual(len(result['rows']), 6)
        self.assertEqual(result['rows'][0]['Status'], 'API error')
        self.assertEqual(result['rows'][1]['Status'], 'Transport error')
        self.assertEqual(result['metrics'][2]['value'], 2)

    def test_zero_quotes_is_a_failure_snapshot_not_a_success(self):
        evidence = fixture()
        for c in evidence['cells']:
            c['observation'].update(http_status=503, response={'message': 'Unavailable'})
        result = quotes.analyze(evidence)
        self.assertEqual(result['quoted'], 0)
        self.assertIn('no usable quotes', result['supports'])
        self.assertEqual(len(result['rows']), 6)

    def test_no_request_for_missing_catalog_asset_is_visible(self):
        evidence = fixture()
        c = evidence['cells'][0]
        c.pop('observation')
        c['not_requested'] = 'Pinned asset missing from live catalog'
        result = quotes.analyze(evidence)
        self.assertEqual(result['attempted'], 5)
        self.assertEqual(result['rows'][0]['Status'], 'Not requested')

    def test_changed_plan_duplicates_and_missing_cells_rejected(self):
        for kind in ('policy', 'missing', 'duplicate'):
            evidence = fixture()
            if kind == 'policy': evidence['policy']['slippage_bps'] = 200
            elif kind == 'missing': evidence['cells'].pop()
            else: evidence['cells'][1] = copy.deepcopy(evidence['cells'][0])
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                quotes.analyze(evidence)

    def test_http_success_is_not_enough_for_a_usable_preview(self):
        for change in ('no_quote', 'wrong_route', 'wrong_input', 'dry_false', 'dry_integer',
                       'deposit_address', 'invalid_min', 'negative_eta', 'nan_eta', 'zero_output'):
            evidence = fixture()
            data = evidence['cells'][0]['observation']['response']
            if change == 'no_quote': data.pop('quote')
            elif change == 'wrong_route': data['quoteRequest']['destinationAsset'] = 'different'
            elif change == 'wrong_input': data['quote']['amountIn'] = '123'
            elif change == 'dry_false': data['quoteRequest']['dry'] = False
            elif change == 'dry_integer': data['quoteRequest']['dry'] = 1
            elif change == 'deposit_address': data['quote']['depositAddress'] = 'do-not-fund'
            elif change == 'invalid_min': data['quote']['minAmountOut'] = '999999999999'
            elif change == 'negative_eta': data['quote']['timeEstimate'] = -1
            elif change == 'nan_eta': data['quote']['timeEstimate'] = float('nan')
            else: data['quote']['amountOut'] = '0'
            with self.subTest(change=change):
                result = quotes.analyze(evidence)
                self.assertEqual(result['quoted'], 5)
                self.assertEqual(result['rows'][0]['Status'], 'Invalid response')

    def test_changed_evidence_request_is_rejected(self):
        evidence = fixture()
        evidence['cells'][0]['observation']['request']['dry'] = False
        with self.assertRaisesRegex(ValueError, 'declared dry matrix'):
            quotes.analyze(evidence)

    def test_micro_usdc_and_large_base_units_are_not_rounded(self):
        self.assertEqual(quotes.format_usdc('1'), '0.000001')
        self.assertEqual(quotes.format_usdc('1234567890123456789012345678901'), '1234567890123456789012345.678901')
        for bad in (1, '-1', '1.1', 'NaN', '１２'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                quotes.format_usdc(bad)

    def test_preview_transport_cannot_be_reused_to_commit_a_quote(self):
        payload = fixture()['cells'][0]['observation']['request']
        with patch('urllib.request.build_opener') as opener:
            for value in (False, 1, None):
                bad = {**payload, 'dry': value}
                with self.assertRaises(ValueError): quote_preview(bad)
            with self.assertRaises(ValueError): fetch_json(QUOTE_URL, payload)
            opener.assert_not_called()
        with self.assertRaises(ValueError):
            NoQuoteRedirect().redirect_request(None, None, 307, '', {}, 'https://example.com')

    def test_http_error_body_is_kept_instead_of_being_replaced(self):
        import io
        import urllib.error
        payload = fixture()['cells'][0]['observation']['request']
        error = urllib.error.HTTPError(QUOTE_URL, 400, 'Bad Request', {}, io.BytesIO(b'{"message":"No route"}'))
        opener = MagicMock()
        opener.open.side_effect = error
        with patch('urllib.request.build_opener', return_value=opener):
            output = quote_preview(payload)
        self.assertEqual(output['http_status'], 400)
        self.assertEqual(output['response']['message'], 'No route')
        self.assertIs(output['request']['dry'], True)
        opener.open.assert_called_once()

    def test_collector_keeps_all_cells_without_retrying_failures(self):
        catalog = [{'assetId': v, 'blockchain': k, 'symbol': 'USDC', 'decimals': 6}
                   for k, v in quotes.ASSETS.items()]
        with patch('experiments.quotes.fetch_json', return_value=catalog), patch('experiments.quotes.quote_preview',
                return_value={'http_status': 400, 'response': {'message': 'Unavailable'}}) as preview:
            evidence = quotes.collect()
        self.assertEqual(len(evidence['cells']), 6)
        self.assertEqual(preview.call_count, 6)
        self.assertTrue(all(call.args[0]['dry'] is True for call in preview.call_args_list))

    def test_changed_catalog_decimals_stop_before_any_quote_request(self):
        catalog = [{'assetId': v, 'blockchain': k, 'symbol': 'USDC', 'decimals': 18}
                   for k, v in quotes.ASSETS.items()]
        with patch('experiments.quotes.fetch_json', return_value=catalog), patch('experiments.quotes.quote_preview') as preview:
            with self.assertRaisesRegex(ValueError, 'metadata changed'): quotes.collect()
            preview.assert_not_called()
