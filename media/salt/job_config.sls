{% set puser = salt['pillar.get']('puser',) %}
{% set project = salt['pillar.get']('project',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set pub_path = salt['pillar.get']('pub_path',) %}
{% set filename = salt['pillar.get']('filename',) %}
{% set ctype = salt['pillar.get']('ctype',) %}

backup_dir:
  file.directory:
    - name: /home/{{ puser }}/backup/config/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - makedirs: True
    - recurse:
      - user
      - group
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}/conf
    - name: if [ -f {{ filename }} ];then /bin/cp -rf {{ filename }} /home/{{ puser }}/backup/config/{{ dpath }}/{{ dtime }}/;fi
    - user: {{ puser }}
    - group: {{ puser }}
    - unless: test ! -d /home/{{ puser }}/backup/config/{{ dpath }}/{{ dtime }}

update_war:
  file.managed:
    - name: /home/{{ puser }}/{{ pub_path }}/conf/{{ filename }}
    - source: salt://config/{{ project }}-{{ dpath }}/{{ filename }}.jinja
    - makedirs: True
    - backup: minion
    - template: jinja
    - require:
      - backup_dir
    #- onchanges:
    #  - backup_dir

