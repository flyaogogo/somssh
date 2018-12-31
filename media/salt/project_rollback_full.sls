{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set ctype = salt['pillar.get']('ctype',) %}

file_delete:
  file.absent:
    - name: /home/{{ puser }}/{{ dpath }}/webapps/
    - unless: test ! -z /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}

last_action:
  file.recurse:
    - name: /home/{{ puser }}/{{ dpath }}/webapps/
    - user: {{ puser }}
    - source: /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}
    - include_empty: True
    - require:
      - file_delete
    - onchanges:
      - file_delete


tomcat_process:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        source /home/{{ puser }}/.bash_profile
        {% if ctype == 0 %}
        cd bin && sh shutdown.sh || sh shutdown.sh
        sh startup.sh
        {% else %}
        kill -TERM `cat RUNNING_PID` && rm -rf RUNNING_PID
        nohup sh start >/dev/null 2>/dev/null &
        {% endif %}
    - user: {{ puser }}
    - require:
      - last_action
    - onchanges:
      - last_action

