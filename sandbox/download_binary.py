"""Cache the pinned official Sandbox binary; extract only its expected regular file."""
import os
import platform
import shutil
import stat
import tarfile
import tempfile
import urllib.request
from pathlib import Path

VERSION = '2.14.0'
ROOT = Path(__file__).resolve().parent


def ensure_binary():
    pairs = {('Linux', 'x86_64'): ('Linux', 'x86_64'), ('Linux', 'aarch64'): ('Linux', 'aarch64'),
             ('Darwin', 'arm64'): ('Darwin', 'arm64')}
    target = pairs.get((platform.system(), platform.machine()))
    if not target:
        raise RuntimeError('Fresh sandbox requires supported Linux/WSL or macOS ARM64')
    destination = ROOT / 'node_modules/near-sandbox/bin' / ('near-sandbox-' + VERSION) / 'near-sandbox'
    if destination.is_file():
        return destination
    if not (ROOT / 'node_modules/near-sandbox/package.json').is_file():
        raise RuntimeError('First run npm ci --ignore-scripts in the sandbox folder')
    url = f'https://s3-us-west-1.amazonaws.com/build.nearprotocol.com/nearcore/{target[0]}-{target[1]}/{VERSION}/near-sandbox.tar.gz'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='onear-download-') as temporary:
        archive = Path(temporary) / 'sandbox.tar.gz'
        request = urllib.request.Request(url, headers={'User-Agent': 'All-in-oNEar/0.5'})
        with urllib.request.urlopen(request, timeout=60) as response, archive.open('wb') as output:
            size = 0
            while True:
                chunk = response.read(1_048_576)
                if not chunk:
                    break
                size += len(chunk)
                if size > 150_000_000:
                    raise RuntimeError('Sandbox archive exceeds the download limit')
                output.write(chunk)
        with tarfile.open(archive, 'r:gz') as compressed:
            candidates = [member for member in compressed if member.isfile() and
                          Path(member.name).name == 'near-sandbox']
            if len(candidates) != 1 or candidates[0].size > 250_000_000:
                raise RuntimeError('Unexpected official sandbox archive layout')
            source = compressed.extractfile(candidates[0])
            staging = destination.with_name('near-sandbox.download')
            try:
                with staging.open('wb') as output:
                    shutil.copyfileobj(source, output)
                staging.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                os.replace(staging, destination)
            finally:
                staging.unlink(missing_ok=True)
    return destination


if __name__ == '__main__':
    print(ensure_binary())
