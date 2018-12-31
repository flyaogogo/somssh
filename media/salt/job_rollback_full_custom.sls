{% set slang = salt['grains.get']('locale_info:defaultlanguage',) %}
{% set sencode = salt['grains.get']('locale_info:defaultencoding',) %}
{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set ifreload = salt['pillar.get']('ifreload',) %}


{% if ifreload == 0 %}
tomcat_shutdown:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        source /etc/profile
        source /home/{{ puser }}/.bash_profile
        kill -TERM `cat RUNNING_PID`
        rm -rf RUNNING_PID
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - user: {{ puser }}
{% endif %}

update_war:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        rm -rf lib plugins
        /bin/cp -rf /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}/{lib,plugins} ./
    - unless: test -z /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}

{% if ifreload == 0 %}
tomcat_startup:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        source /etc/profile
        source /home/{{ puser }}/.bash_profile
        nohup /bin/bash start >/dev/null 2>/dev/null &
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - user: {{ puser }}
    - require:
      - update_war
    - onchanges:
      - update_war
{% endif %}
