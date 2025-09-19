# Release Checklist

Copy this checklist for each release:

## Pre-Release
- [ ] All tests pass locally
- [ ] Code is properly formatted (`make format`)
- [ ] Linting passes (`make lint`) 
- [ ] Documentation is up to date
- [ ] Git working directory is clean
- [ ] Choose appropriate version number (semantic versioning)

## Release Process
- [ ] Test release process: `make release-dry-run version=X.Y.Z`
- [ ] Release to Test PyPI: `make release-test version=X.Y.Z`
- [ ] Test installation from Test PyPI:
  ```bash
  pip install -i https://test.pypi.org/simple/ bookforge
  bookforge --help
  ```
- [ ] Release to PyPI: `make release version=X.Y.Z`

## Post-Release Verification
- [ ] Verify package appears on PyPI: https://pypi.org/project/bookforge/
- [ ] Test installation from PyPI: `pip install bookforge`
- [ ] Test CLI functionality: `bookforge --help`
- [ ] Test import in Python: `import bookforge`
- [ ] Verify GitHub tag and release created
- [ ] Update any dependent projects

## Notes
Version: ___________
Date: ___________
Changes: 
- 
- 
- 

Issues found:
- 
- 
- 