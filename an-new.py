#!/usr/bin/env python3
import os
import re
import jinja2
import argparse
import sys
from datetime import datetime

ANALYSIS_DIR = '$HOME/analysis'
DIR_FORMAT = '{{ date.strftime("%Y_%m_%d") }}-{{ name_slug }}'
CREATE_DIRS = ['artifacts', 'files', 'temp']
INDICATORS_YAML = '''---
ips:
{%- for i in ips %}
  - "{{ i }}"
{%- endfor %}
domains:
{%- for i in domains %}
  - "{{ i }}"
{%- endfor %}
actors:
{%- for i in actors %}
  - "{{ i }}"
{%- endfor %}
emails:
{%- for i in emails %}
  - "{{ i }}"
{%- endfor %}
urls:
{%- for i in urls %}
  - "{{ i }}"
{%- endfor %}
'''

TIMELINE_YAML = '''---
timeline:
  - date: {{ date.strftime("%z") }}
    note: "Investigation Started"
'''

REPORT_MD = '''
# {{ name }}

## Executive Summary:

On {{ date.strftime("%m/%d/%Y") }} {{ user }} via {{ escalation }} of a security event. This incident was initially classified as a {{ priority }} severity event and required action due to the sensitive nature of the investigation.

### Timeline

* {{ date.strftime("%m/%d/%Y %H:%M" }}: Initial incident investigation created


# Observations


# Root Causes:

'''


def create_scaffolding(context):
    indicators = jinja2.Template(INDICATORS_YAML).render(**context)
    report = jinja2.Template(REPORT_MD).render(**context)
    timeline = jinja2.Template(TIMELINE_YAML).render(**context)
    base_dir = os.path.abspath(os.path.expandvars(os.path.expanduser(ANALYSIS_DIR)))
    dir_name = jinja2.Template(DIR_FORMAT).render(**context)
    base_dir = os.path.join(base_dir, dir_name)
    if os.path.exists(base_dir):
        print('Error! Path "{}" exists, aborting.'.format(base_dir))
        sys.exit(1)
    # Create Directories
    for d in CREATE_DIRS:
        os.makedirs(os.path.join(base_dir, d))
    # Write templates to dir
    with open(os.path.join(base_dir, 'indicators.yaml'), 'w') as fd:
        fd.write(indicators)
    with open(os.path.join(base_dir, 'timeline.yaml'), 'w') as fd:
        fd.write(timeline)
    with open(os.path.join(base_dir, 'report.md'), 'w') as fd:
        fd.write(report)


def input_multiline():
    res = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        res.append(line)
    if not res:
        # Return a couple empty strings so the template has example data
        return ['', '', ]
    return res


def get_user_input(context):
    inputs = ['IPs', 'Domains', 'URLs', 'Emails', 'Actors']
    for i in inputs:
        print('{} (Ctrl-D to end):'.format(i))
        context[i.lower()] = input_multiline()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', nargs='+')
    parser.add_argument('--no-input', '-n', action="store_false", default=True, dest="interactive")
    parser.add_argument('--priority', '-p', dest='priority', default='medium')
    args = parser.parse_args()
    context = {
        'name': ' '.join(args.name),
        'date': datetime.now(),
        'ips': ['', ''],
        'priority': args.priority,
        'domains': ['', ''],
        'actors': ['', ''],
        'emails': ['', ''],
        'urls': ['', '']
    }
    name_slug = context['name'].lower().strip()
    name_slug = re.sub(r'[\s-]', '_', name_slug)
    name_slug = re.sub(r'[_]+', '_', name_slug)
    name_slug = name_slug.lower().strip()
    context['name_slug'] = name_slug
    if args.interactive:
        get_user_input(context)
    create_scaffolding(context)


if __name__ == '__main__':
    main()
