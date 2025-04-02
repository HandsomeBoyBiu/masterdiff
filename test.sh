# git clone https://github.com/Exiv2/exiv2.git
rm -rf test
mkdir test
python3 masterdiff.py --repo $PWD/exiv2 --last 3 --output ./test/
