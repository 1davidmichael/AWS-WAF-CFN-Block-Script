# Troposphere IP Blocking WAF

Python script which takes a list of CIDR ranges and creates a CFN template
to block them via AWS WAF

```
virtualenv venv
source venv/bin/activate
pip install -r requirments.txt

# Add IP addresses to file.txt
python create.py > template.yaml
```
