# Release procedure

* Update VERSION in setup.py
* Commit with appropriate message
```
git commit -am "Release X.Y.Z"
```
* Create tag and push everything to Github
```
git tag -a X.Y.Z -m "eth-docgen release X.Y.Z"
git push --tags origin
git push
```
* Make distribution
```
python setup.py sdist bdist_wheel
```
* Upload to PyPI
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

# Release notes

## 0.1.3
Fix crash issue related to dev docs

## 0.1.2
Fix packaging and distribution issues

## 0.1.1
Attempt to fix packaging issues

## 0.1.0
Initial release