import random
import glob
import gzip
import json
import hashlib
import logging
import tempfile
import os
from cStringIO import StringIO

log = logging.getLogger('spiked1000g')

GENOTYPE = {
    "het": "0|1",
    "hom": "1|1"
}


CHROM = [str(x) for x in range(22)]+["X", "Y"]

def get_vcf_lines(variant):
    template = "{chrom}\t{pos}\t.\t{ref}\t{alt}\t100\tPASS\t.\tGT\t{gt}\n"
    return template.format(
        chrom = variant["chromosome"],
        pos = variant["position"],
        ref = variant["ref"],
        alt = variant["alt"],
        gt = GENOTYPE[variant["genotype"]]
    )


def fetch_background(sex):
    samples = json.load(open("/spiked1000g/src/1000g_samples.json", "r"))
    candidates = [s for s in samples if samples[s]["sex"] == sex]
    sample_id = candidates[random.randint(0,len(candidates)-1)]

    return sample_id

def get_vcf(sample_id):
    return glob.glob("/samples/"+sample_id+"*")[0]


def generate_vcf_discarded(case, sample_id, hash):
    # cases = json.load(open("/spiked1000g/src/cases.json", 'r'))
    # case = cases[case]
    sex = case["patient"]["sex"]
    variants = case["variants"]
    variants_vcf = [(v["chromosome"], v["position"], get_vcf_lines(v)) for v in variants]
    phenotypes = case["phenotypes"]
    vcf = get_vcf(sample_id)

    #output = tempfile.NamedTemporaryFile(delete=False)
    output = StringIO()
    with gzip.open(vcf, 'r') as background:
        for l in background:
            if l.startswith('#CHROM'):
                output.write("##HASH={}\n".format(hash))
                output.write("##BACKGROUND={}\n".format(sample_id))
                output.write("##SEX={}\n".format(sex))
                output.write("##PHENOTYPES={}\n".format('|'.join(phenotypes)))
                output.write("##VARIANTS={}\n".format("|".join(["-".join(str(x) for x in [v["chromosome"], v["position"], v["ref"], v["alt"], v["genotype"]]) for v in variants])))

            if not l.startswith('#'):
                chrom, pos = l.split('\t')[:2]
                pos = int(pos)
                variants_to_write = []
                for i, v in enumerate(variants_vcf):
                    if CHROM.index(chrom) > CHROM.index(v[0]):
                        variants_to_write.append(i)
                    elif CHROM.index(chrom) == CHROM.index(v[0]) and pos > v[1]:
                        variants_to_write.append(i)

                for i in reversed(sorted(variants_to_write)):

                    v = variants_vcf.pop(i)
                    output.write(v[2])

            output.write(l)

        for v in variants_vcf:
            output.write(v[2])

    output.seek(0)
    return output


def generate_vcf(case, sample_id, hash):
    sex = case["patient"]["sex"]
    variants = case["variants"]
    phenotypes = case["phenotypes"]

    header = "##fileformat=VCFv4.2\n"
    header += "##HASH={}\n".format(hash)
    header += "##BACKGROUND={}\n".format(sample_id)
    header += "##SEX={}\n".format(sex)
    header += "##PHENOTYPES={}\n".format('|'.join(phenotypes))
    header += "##VARIANTS={}\n".format("|".join(["-".join(str(x) for x in [v["chromosome"], v["position"], v["ref"], v["alt"], v["genotype"]]) for v in variants]))
    header += "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{}\n".format(sample_id)
    data = header
    for v in variants:
        data += get_vcf_lines(v)

    f = tempfile.NamedTemporaryFile(delete=False, suffix='.vcf')
    f2 = tempfile.NamedTemporaryFile(delete=False, suffix='.vcf.gz')
    f.write(data)
    f.close()
    f2.close()
    vcf = get_vcf(sample_id)

    os.system("bgzip {}".format(f.name))
    os.system("vcf-concat {} {} | vcf-sort -c | bgzip -c > {}".format(f.name+'.gz', vcf, f2.name))

    return f2.name


def get_case_and_sample(hash):
    case_hash, sample_id_hash = hash[:10], hash[10:]
    cases = json.load(open("/spiked1000g/src/cases.json", 'r'))
    case_id = next(k for k,v in cases.iteritems() if hashlib.sha1(json.dumps(v)).hexdigest()[:10] == case_hash)

    samples = json.load(open('/spiked1000g/src/1000g_samples.json', 'r'))
    sample_id = next(k for k in samples if hashlib.sha1(k).hexdigest()[:10] == sample_id_hash)

    return case_id, sample_id


def spike(case_id, sample_id, hash):
    if hash:
        case_id, sample_id = get_case_and_sample(hash)

    cases = json.load(open("/spiked1000g/src/cases.json", 'r'))
    if not case_id:
        N = random.randint(0, len(cases)-1)
        case_id = cases.keys()[N]
        case = cases[cases.keys()[N]]
    else:
        case = cases[case_id]

    samples = json.load(open('/spiked1000g/src/1000g_samples.json', 'r'))
    if not sample_id:
        sample_id = fetch_background(case["patient"]["sex"])


    if not hash:
        hash = hashlib.sha1(json.dumps(case)).hexdigest()[:10]+hashlib.sha1(sample_id).hexdigest()[:10]

    assert samples[sample_id]["sex"] == case["patient"]["sex"], "{}!={}".format(samples[sample_id]["sex"], case["patient"]["sex"])

    logging.info("Injecting case {} into {} ({})".format(case_id, sample_id, hash))

    f = generate_vcf(case, sample_id, hash)
    return f, case_id, sample_id, hash


