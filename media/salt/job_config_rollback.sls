{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set pub_path = salt['pillar.get']('pub_path',) %}
{% set filename = salt['pillar.get']('filename',) %}
{% set ctype = salt['pillar.get']('ctype',) %}

update_war:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}/conf/
    - name: /bin/cp -rf /home/{{ puser }}/backup/config/{{ dpath }}/{{ dtime }}/{{ filename }} ./{{ filename }}
    - user: {{ puser }}
    - group: {{ puser }}

