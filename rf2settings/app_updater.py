"""
These methods are not used for now.

Using requests lib triggers Windows Security. However we can download any arbitrary data using
sockets. -_-

"""

"""
Remove auto-updates for now
@eel.expose
def check_for_updates():
    # Report to FrontEnd if a new version is available
    up = GitHubUpdater()
    if up.is_current_version():
        return json.dumps({'result': False, 'version': up.version})

    return json.dumps({'result': True, 'version': up.git_version})


@eel.expose
def download_update():
    # Download the updated setup
    up = GitHubUpdater()
    if not up.is_current_version():
        return json.dumps({'result': up.download_update()})
    return json.dumps({'result': False})


@eel.expose
def run_update():
    # Close the App and run the updated setup
    if GitHubUpdater.execute_update_setup():
        request_close()
        return json.dumps({'result': True})
    return json.dumps({'result': False})
"""
