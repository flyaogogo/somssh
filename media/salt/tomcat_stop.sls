{% set slang = salt['grains.get']('locale_info:defaultlanguage',) %}
{% set sencode = salt['grains.get']('locale_info:defaultencoding',) %}
{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set ctype = salt['pillar.get']('ctype',) %}

tomcat_stop:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        source /etc/profile
        source /home/{{ puser }}/.bash_profile
        {% if ctype == 0 %}
        p=`ps ax|grep /home/{{ puser }}/{{ dpath }}/bin/|grep -v 'grep'|awk '{print $1}'`
        [ -z $p ] || (echo "Process kill now..." && kill -9 $p)
        [ -f PID ] && rm -rf PID
        rm -rf /home/{{ puser }}/{{ dpath }}/work/Catalina/localhost
        {% else %}
        kill -TERM `cat RUNNING_PID`
        rm -rf RUNNING_PID
        {% endif %}
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - user: {{ puser }}