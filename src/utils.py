import os
from fastapi.responses import RedirectResponse
from fastapi import status

def redirect_to_login():
    # redirect 是一种 response
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    # RedirectResponse 还能附着着 delete_cookie
    redirect_response.delete_cookie(key='access_token')
    return redirect_response

def read_env_file(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=')
                os.environ[key] = value