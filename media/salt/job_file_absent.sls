{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set dname = salt['pillar.get']('dname',) %}

last_action:
  file.absent:
    - name: /home/{{ puser }}/{{ dpath }}/webapps/{{ dname }}
    - require:
      - update_war
    - onchanges:
      - update_war
