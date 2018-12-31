{% set slang = salt['grains.get']('locale_info:defaultlanguage',) %}
{% set sencode = salt['grains.get']('locale_info:defaultencoding',) %}
{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set ctype = salt['pillar.get']('ctype',) %}

tomcat_start:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        source /etc/profile
        source /home/{{ puser }}/.bash_profile
        echo " " > logs/soms_log
        wc -l logs/catalina.out|awk '{print $1}' > logs/soms_num
        {% if ctype == 0 %}
        cd bin && /bin/bash startup.sh
        {% else %}
        nohup /bin/bash start >/dev/null 2>/dev/null &
        {% endif %}
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - user: {{ puser }}