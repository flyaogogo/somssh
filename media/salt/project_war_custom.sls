{% set puser = salt['pillar.get']('puser',) %}
{% set war = salt['pillar.get']('sname',) %}
{% set spath = salt['pillar.get']('spath',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set pub_path = salt['pillar.get']('pub_path',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set ifreload = salt['pillar.get']('ifreload',) %}

file_backup:
  file.directory:
    - name: /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - makedirs: True
    - recurse:
      - user
      - group
  cmd.run:
    - name: /bin/cp -rf /home/{{ puser }}/{{ dpath }}/{{ pub_path }}/* /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - unless: test ! -d /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}

delete_file:
  file.absent:
    - name: /home/{{ puser }}/{{ dpath }}/{{ pub_path }}/
    - require:
      - file_backup
    - onchanges:
      - file_backup

last_action:
  archive.extracted:
    - name: /home/{{ puser }}/{{ dpath }}/{{ pub_path }}/
    - user: {{ puser }}
    - group: {{ puser }}
    - enforce_toplevel: False
    - source: {{ spath }}/{{ pub_path }}/{{ war }}.tar.gz
    - source_hash: {{ spath }}/{{ pub_path }}/{{ war }}.hash
    - backup: minion
    - require:
      - delete_file
    - onchanges:
      - delete_file

{% if ifreload ==  '1' %}
include:
  - tomcat_process
{% endif %}


