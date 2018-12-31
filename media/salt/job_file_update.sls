{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set sname = salt['pillar.get']('sname',) %}
{% set dname = salt['pillar.get']('dname',) %}
{% set dtime = salt['pillar.get']('dtime',) %}

update_war:

  file.managed:
    - name: /home/{{ puser }}/{{ dpath }}/webapps/{{ dname }}.war
    - source: salt://full/{{ dpath }}/{{ sname }}.war
    - user: {{ puser }}
    - group: {{ puser }}
    - mode: 0644
    - backup: minion


last_action:
  file.absent:
    - name: /home/{{ puser }}/{{ dpath }}/webapps/{{ dname }}
    - require:
      - update_war
    - onchanges:
      - update_war

