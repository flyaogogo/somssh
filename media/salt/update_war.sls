update_war:
  {% set puser = salt['pillar.get']('puser',) %}
  {% set spath = salt['pillar.get']('spath',) %}
  {% set dpath = salt['pillar.get']('dpath',) %}
  {% set sname = salt['pillar.get']('sname',) %}
  {% set dname = salt['pillar.get']('dname',) %}
  {% set dtime = salt['pillar.get']('dtime',) %}
  {% set ifreload = salt['pillar.get']('ifreload',) %}

  file.managed:
    - name: /home/{{ puser }}/{{ dpath }}/webapps/{{ dname }}.war
    - source: {{ spath }}/{{ sname }}.war
    - source_hash: {{ spath }}/{{ sname }}.hash
    #- skip_verify: True
    - user: {{ puser }}
    - group: {{ puser }}
    - mode: 0755
    - backup: minion

backup_dir:
  file.directory:
    - name: /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - makedirs: True
    - recurse:
      - user
      - group
    - require:
      - update_war
    - onchanges:
      - update_war
  cmd.run:
    - name: /bin/cp -rf /home/{{ puser }}/{{ dpath }}/webapps/{{ dname }}* /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - unless: test ! -d /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}

last_action:
  file.absent:
    - name: /home/{{ puser }}/{{ dpath }}/webapps/{{ dname }}
    - require:
      - backup_dir
    - onchanges:
      - backup_dir

{% if ifreload ==  '1' %}
include:
  - tomcat_process
{% endif %}

