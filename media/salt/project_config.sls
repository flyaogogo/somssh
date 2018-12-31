{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set dname = salt['pillar.get']('dname',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set ifreload = salt['pillar.get']('ifreload',) %}

file_backup:
  file.directory:
    - name: /home/{{ puser }}/backup/config/{{ dpath }}/{{ dtime }}/
    - user: {{ puser }}
    - group: {{ puser }}
    - makedirs: True
    - recurse:
      - user
      - group
  cmd.run:
    - name: /bin/cp -rf /home/{{ puser }}/{{ dpath }}/conf/{{ dname }} /home/{{ puser }}/backup/config/{{ dpath }}/{{ dtime }}/
    - user: {{ puser }}
    - group: {{ puser }}
    - unless: test ! -d /home/{{ puser }}/backup/config/{{ dpath }}/{{ dtime }}/

last_action:
  file.managed:
    - name: /home/{{ puser }}/{{ dpath }}/conf/{{ dname }}
    - source: salt://config/{{ dpath }}/{{ dname }}
    - user: {{ puser }}
    - group: {{ puser }}
    - mode: 0600
    - backup: minion
    - require:
      - file_backup
    - onchanges:
      - file_backup

{% if ifreload ==  '1' %}
include:
  - tomcat_process
{% endif %}
