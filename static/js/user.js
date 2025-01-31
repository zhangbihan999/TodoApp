// Change basic info
const basic_info_form = document.getElementById('basic_info')

if (basic_info_form) {
    basic_info_form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const payload = {
            email: data.email,
            username: data.username,
            first_name: data.first_name,
            last_name: data.last_name,
            role: data.role,
            phone_number: data.phone_number
        }

        try {
            const response = await fetch('/user/change-basic-info', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getCookie('access_token')}`
                },
                body: JSON.stringify(payload)
            })

            if (response.ok) {
                location.reload();
            } else {
                // Handle error
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    })
}

// Change password
const change_password_form = document.getElementById('change_password')

if (change_password_form) {
    change_password_form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        if (data.new_password != data.new_password2) {
            alert(`两次输入的新密码不一致！`);
            return;
        }

        const payload = {
            password: data.current_password,
            new_password: data.new_password
        } 

        try {
            const response = await fetch('/user/change-password', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getCookie('access_token')}`
                },
                body: JSON.stringify(payload)
            })

            if (response.ok) {
                alert(`密码修改成功！请关闭提示栏后重新登录。`)
                logout();
            } else {
                // Handle error
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    })
}

function logout() {
    // Get all cookies
    const cookies = document.cookie.split(";");

    // Iterate through all cookies and delete each one
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        // Set the cookie's expiry date to a past date to delete it
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
    }

    // Redirect to the login page
    window.location.href = '/auth/login-page';
};