{% set slang = salt['grains.get']('locale_info:defaultlanguage',) %}
{% set sencode = salt['grains.get']('locale_info:defaultencoding',) %}
{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set dname = salt['pillar.get']('dname',) %}
{% set dtime = salt['pillar.get']('dtime',) %}
{% set ifreload = salt['pillar.get']('ifreload',) %}


{% if ifreload == 0 %}
tomcat_shutdown:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}
    - name: |
        source /etc/profile
        source /home/{{ puser }}/.bash_profile
        p=`ps ax|grep /home/{{ puser }}/{{ dpath }}/bin/|grep -v 'grep'|awk '{print $1}'`
        [ -z $p ] || (echo "Process kill now..." && kill -9 $p)
        [ -f PID ] && rm -rf PID
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - user: {{ puser }}
{% endif %}

update_war:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}/{{ dname }}
    - name: |
        rm -rf *
        /bin/cp -rf /home/{{ puser }}/backup/increase/{{ dpath }}/{{ dtime }}/* ./
    - unless: test -z /home/{{ puser }}/backup/increase/{{ dpath }}/{{ dtime }}/
    - user: {{ puser }}
    - group: {{ puser }}

{% if ifreload == 0 %}
tomcat_startup:
  cmd.run:
    - cwd: /home/{{ puser }}/{{ dpath }}/bin
    - name: |
        source /etc/profile
        source /home/{{ puser }}/.bash_profile
        /bin/bash startup.sh
    - shell: /bin/bash
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    - user: {{ puser }}
    - require:
      - update_war
    - onchanges:
      - update_war
{% endif %}
