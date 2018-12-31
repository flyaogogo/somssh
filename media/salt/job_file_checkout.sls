{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set sname = salt['pillar.get']('sname',) %}
{% set dname = salt['pillar.get']('dname',) %}
{% set dtime = salt['pillar.get']('dtime',) %}

update_war:

  file.managed:
    - name: ./full/{{ dpath }}/{{ sname }}.war
    - source: {{ spath }}/{{ sname }}.war
    - source_hash: {{ spath }}/{{ sname }}.hash
    - user: www
    - group: www
    - mode: 0644

