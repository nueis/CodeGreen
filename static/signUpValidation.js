document.addEventListener("DOMContentLoaded", function () {
    // Error messages initially hidden
    document.querySelectorAll(".error-msg").forEach(function (element) {
        element.style.display = "none";
    });

    // Domain select change event listener
    document.getElementById('domain-select').addEventListener('change', function () {
        const customDomainInput = document.getElementById('custom-domain');
        if (this.value === 'custom') {
            customDomainInput.style.display = 'inline-block';
            this.style.display = 'none';
        } else {
            customDomainInput.style.display = 'none';
        }
    });

    // Form submission event listener
    document.getElementById('signup-form').addEventListener('submit', async function (event) {
        event.preventDefault(); // 기본 폼 제출 방지

        let hasError = false;

        // User ID validation
        const userId = document.getElementById('id').value.trim();
        if (userId === "") {
            document.getElementById('id-error').style.display = "block";
            hasError = true;
        } else {
            document.getElementById('id-error').style.display = "none";
        }

        // Password validation
        const password = document.getElementById('password').value.trim();
        if (password === "") {
            document.getElementById('password-error').style.display = "block";
            hasError = true;
        } else {
            document.getElementById('password-error').style.display = "none";
        }

        // Confirm Password validation
        const confirmPassword = document.getElementById('confirm-password').value.trim();
        if (confirmPassword !== password || confirmPassword === "") {
            document.getElementById('confirm-password-error').style.display = "block";
            hasError = true;
        } else {
            document.getElementById('confirm-password-error').style.display = "none";
        }

        // Nickname validation
        const nickname = document.getElementById('nickname').value.trim();
        if (nickname === "") {
            document.getElementById('nickname-error').style.display = "block";
            hasError = true;
        } else {
            document.getElementById('nickname-error').style.display = "none";
        }

        // Prevent form submission if there are errors
        if (hasError) {
            return;
        }

        // 데이터 수집
        const email = document.getElementById('email').value.trim();
        const domain = document.getElementById('domain-select').value === 'custom'
            ? document.getElementById('custom-domain').value.trim()
            : document.getElementById('domain-select').value;
        const role = document.querySelector('input[name="role"]:checked').value;

        const data = {
            id: userId,
            password: password,
            confirm_password: confirmPassword,
            nickname: nickname,
            email: `${email}@${domain}`,
            role: role,
        };

        try {
            // 서버로 데이터 전송
            const response = await fetch("/service/signup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(errorData.message || "회원가입에 실패했습니다.");
                return;
            }

            // 가입 성공 시 login.html로 리다이렉트
            alert("회원가입에 성공했습니다!");
            window.location.href = "/page/login";
        } catch (error) {
            console.error("Error during signup:", error);
            alert("회원가입 중 문제가 발생했습니다. 다시 시도해주세요.");
        }
    });
});