{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set ctype = salt['pillar.get']('ctype',) %}

tomcat_process:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        {% if ctype == 0 %}
        cd bin && sh shutdown.sh || sh shutdown.sh
        sh startup.sh
        {% else %}
        kill -TERM `cat RUNNING_PID` && rm -rf RUNNING_PID
        nohup sh start >/dev/null 2>/dev/null &
        {% endif %}
    - user: {{ puser }}
