{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set dname = salt['pillar.get']('dname',) %}
{% set dname_old = salt['pillar.get']('dname_old',) %}
{% set pub_path = salt['pillar.get']('pub_path',) %}
{% set ifreload = salt['pillar.get']('ifreload',) %}

file_exists:
  file.exists:
    - name: /home/{{ puser }}/{{ dpath }}/{{ pub_path }}/{{ dname_old }}

file_backup:
  file.directory:
    - name: /home/{{ puser }}/backup/increase/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - makedirs: True
    - recurse:
      - user
      - group
    - require:
      - file_exists
  cmd.run:
    - name: /bin/cp -rf /home/{{ puser }}/{{ dpath }}/{{ pub_path }}/{{ dname_old }} /home/{{ puser }}/backup/increase/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - unless: test ! -d /home/{{ puser }}/backup/increase/{{ dpath }}/{{ dtime }}

file_delete:
  file.absent:
    - name: /home/{{ puser }}/{{ dpath }}/{{ pub_path }}/{{ dname_old }}
    - require:
      - file_backup
    - onchanges:
      - file_backup

last_action:
  file.managed:
    - name: /home/{{ puser }}/{{ dpath }}/{{ pub_path }}/{{ dname }}
    - source: salt://increase/jar/{{ dpath }}/{{ dtime }}/{{ dname }}
    - user: {{ puser }}
    - group: {{ puser }}
    - require:
      - file_delete
    - onchanges:
      - file_delete

{% if ifreload ==  '1' %}
include:
  - tomcat_process
{% endif %}

