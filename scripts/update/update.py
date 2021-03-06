"""

#### NOT IN USE, see ../../update.sh ####

Deploys fhr-jelly for Firefox Health Report

Requires commander_ which is installed on the systems that need it.

.. _commander: https://github.com/oremj/commander
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commander.deploy import task, hostgroups
import commander_settings as settings


@task
def update_code(ctx, tag):
    """Update the code to a specific git reference (tag/sha/etc)."""
    with ctx.lcd(os.path.join(settings.SRC_DIR, 'fhr-jelly')):
        ctx.local('git fetch')
        ctx.local('git pull -f')


@task
def update_locales(ctx):
    """Update a locale directory from SVN."""
    with ctx.lcd(os.path.join(settings.SRC_DIR, 'locale')):
        ctx.local('svn up')


@task
def generate_files(ctx):
    """Use the local, IT-written deploy script to check in changes."""
    command = './generate.py --output-dir %s -f --nowarn '
    with ctx.lcd(os.path.join(settings.SRC_DIR, 'fhr-jelly')):
        ctx.local(command % (settings.SRC_DIR + '/web-output'))


@task
def checkin_changes(ctx):
    """Use the local, IT-written deploy script to check in changes."""
    ctx.local(settings.DEPLOY_SCRIPT)


@hostgroups(settings.WEB_HOSTGROUP,
            remote_kwargs={'ssh_key': settings.SSH_KEY})
def deploy_app(ctx):
    """Call the remote update script to push changes to webheads."""
    ctx.remote(settings.REMOTE_UPDATE_SCRIPT)


@task
def update_info(ctx):
    """Write info about the current state to a publicly visible file."""
    with ctx.lcd(os.path.join(settings.SRC_DIR, 'fhr-jelly')):
        ctx.local('date > ../logs/revision.txt')
        ctx.local('git branch >> ../logs/revision.txt')
        ctx.local('git log -3 >> ../logs/revision.txt')
        ctx.local('git status >> ../logs/revision.txt')
        ctx.local('git rev-parse HEAD > ../logs/revision')


@task
def pre_update(ctx, ref=settings.UPDATE_REF):
    """Update code to pick up changes to this file."""
    update_code(ref)
    update_info()


@task
def update(ctx):
    generate_files()
    checkin_changes()


@task
def deploy(ctx):
    deploy_app()


@task
def update_site(ctx, tag):
    """Update the app to prep for deployment."""
    pre_update(tag)
    update()
