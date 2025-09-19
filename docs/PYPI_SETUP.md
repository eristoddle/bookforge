# PyPI Configuration Setup

## 1. Create PyPI Account
- Main PyPI: https://pypi.org/account/register/
- Test PyPI: https://test.pypi.org/account/register/

## 2. Generate API Tokens
- PyPI: https://pypi.org/manage/account/token/
- Test PyPI: https://test.pypi.org/manage/account/token/

## 3. Create ~/.pypirc

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_API_TOKEN_HERE
```

**Security Notes:**
- Keep API tokens secure and private
- Use tokens instead of passwords
- Add `~/.pypirc` to your `.gitignore`
- Consider using environment variables for CI/CD

## 4. Test Configuration

```bash
# Test with Test PyPI first
python -m twine upload --repository testpypi dist/*

# Then upload to main PyPI
python -m twine upload dist/*
```

## Environment Variables (Alternative)

Instead of `~/.pypirc`, you can use environment variables:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_API_TOKEN_HERE

# For Test PyPI
export TWINE_REPOSITORY_URL=https://test.pypi.org/legacy/
```