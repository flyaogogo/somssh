last_action:
  {% set puser = salt['pillar.get']('puser',) %}
  {% set dpath = salt['pillar.get']('dpath',) %}
  {% set dname = salt['pillar.get']('dname',) %}
  {% set ifreload = salt['pillar.get']('ifreload',) %}

  file.managed:
    - name: /home/{{ puser }}/{{ dpath }}/conf/{{ dname }}
    - source: salt://config/{{ dpath }}/{{ dname }}
    - user: {{ puser }}
    - group: {{ puser }}
    - mode: 0600
    - backup: minion

{% if ifreload ==  '1' %}
include:
  - tomcat_process
{% endif %}
