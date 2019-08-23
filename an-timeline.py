#!/usr/bin/env python3
import os
import jinja2
import sys
from datetime import datetime

TIMELINE_YAML = '''
- date: {{ date.isoformat() }}
  comment: "{{ comment }}"
'''


def main():
    context = {
        'date': datetime.now(),
        'comment': '{}'.format(' '.join(sys.argv[1:])),
    }
    pwd = os.getcwd()
    timeline = os.path.join(pwd, 'timeline.yaml')
    if not os.path.exists(timeline):
        print('No timeline exists... is there anything in your working directory?')
        sys.exit(1)
    content = jinja2.Template(TIMELINE_YAML).render(**context)
    with open(timeline, 'a') as fd:
        print('Writing')
        fd.write(content)

    print(pwd)


if __name__ == '__main__':
    main()
