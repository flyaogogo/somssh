{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set pub_path = salt['pillar.get']('pub_path',) %}
{% set ifreload = salt['pillar.get']('ifreload',) %}

file_backup:
  file.directory:
    - name: /home/{{ puser }}/backup/increase/{{ dpath }}/{{ dtime }}/
    - user: {{ puser }}
    - group: {{ puser }}
    - makedirs: True
    - recurse:
      - user
      - group
  cmd.run:
    - name: /bin/cp -rf /home/{{ puser }}/{{ dpath }}/{{ pub_path }} /home/{{ puser }}/backup/increase/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - unless: test ! -d /home/{{ puser }}/backup/increase/{{ dpath }}/{{ dtime }}

last_action:
  file.recurse:
    - name: /home/{{ puser }}/{{ dpath }}/{{ pub_path }}
    - user: {{ puser }}
    - group: {{ puser }}
    - dir_mode: 2755
    - source: salt://increase/normal/{{ dpath }}/{{ dtime }}
    - include_empty: True
    - backup: minion
    - require:
      - file_backup
    - onchanges:
      - file_backup

{% if ifreload ==  '1' %}
include:
  - tomcat_process
{% endif %}

