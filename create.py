import netaddr

from troposphere import (
    Template,
    Ref,
)

from troposphere.waf import (
    Rule,
    IPSet,
    IPSetDescriptors,
    Rules,
    WebACL,
    Action,
    Predicates
)


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


t = Template()
t.add_version('2010-09-09')
t.add_description(
    "Create an AWS Waf configuration that blocks IP addresses from a file list"
)

ip_set_descriptors = []

cidr_ranges = open('file.txt').readlines()

netaddr_cidr_ranges = []
for cidr_range in cidr_ranges:

    netaddr_cidr_ranges.append(netaddr.IPNetwork(cidr_range.rstrip()))

merged_list = netaddr.cidr_merge(netaddr_cidr_ranges)

for cidr_range in merged_list:
    ip_set_descriptors.append(
        IPSetDescriptors(
            Type="IPV4",
            Value=str(cidr_range)
        )
    )

# Divide the cidr list to accomodate the AWS IP set limit
# https://docs.aws.amazon.com/waf/latest/developerguide/limits.html
chunked_ip_set_descriptors = list(divide_chunks(ip_set_descriptors, 10000))

ip_sets = []
for index, item in enumerate(chunked_ip_set_descriptors):
    ip_sets.append(t.add_resource(
        IPSet(
            "IPSet%s" % index,
            Name="IPSet",
            IPSetDescriptors=ip_set_descriptors
        )
    ))

predicates = []
for index, item in enumerate(ip_sets):
    predicates.append(
        Predicates(
            DataId=Ref(item),
            Type="IPMatch",
            Negated=False
        )
    )

waf_rule = t.add_resource(
    Rule(
        'Rule',
        Name='exampleRule',
        MetricName='exampleRule',
        Predicates=predicates
    )
)

t.add_resource(
    WebACL(
        "exampleWebACL",
        Name="exampleWebACL",
        MetricName='exampleWebACL',
        DefaultAction=Action(
            Type="ALLOW"
        ),
        Rules=[
            Rules(
                Action=Action(
                    Type="COUNT",
                ),
                Priority=1,
                RuleId=Ref(waf_rule)
            )
        ]
    )
)

print(t.to_yaml())
