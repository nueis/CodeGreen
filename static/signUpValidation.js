document.addEventListener("DOMContentLoaded", function () {
    // ID 중복 확인 버튼 이벤트
    const checkButton = document.querySelector("#id + .check-btn");
    if (checkButton) {
        checkButton.addEventListener("click", async function () {
            const userId = document.getElementById("id").value.trim();

            if (userId === "") {
                alert("아이디를 입력해주세요.");
                return;
            }

            try {
                // 서버에 GET 요청 보내기
                const response = await fetch(`/service/checkid?id=${encodeURIComponent(userId)}`);
                const data = await response.json();

                if (response.ok) {
                    alert(data.message); // 중복 여부 메시지 출력
                } else {
                    alert(data.message || "중복 확인 중 오류가 발생했습니다.");
                }
            } catch (error) {
                console.error("Error during ID check:", error);
                alert("중복 확인 중 문제가 발생했습니다. 다시 시도해주세요.");
            }
        });
    } else {
        console.error("Check button not found!");
    }

    // 닉네임 중복 확인 버튼 이벤트
    const checkNicknameButton = document.querySelector("#nickname + .check-btn");
    if (checkNicknameButton) {
        checkNicknameButton.addEventListener("click", async function () {
            const nickname = document.getElementById("nickname").value.trim();

            if (nickname === "") {
                alert("닉네임을 입력해주세요.");
                return;
            }

            try {
                const response = await fetch(`/service/checknickname?nickname=${encodeURIComponent(nickname)}`);
                const data = await response.json();

                if (response.ok) {
                    alert(data.message); // 중복 여부 메시지 출력
                } else {
                    alert(data.message || "중복 확인 중 오류가 발생했습니다.");
                }
            } catch (error) {
                console.error("Error during nickname check:", error);
                alert("중복 확인 중 문제가 발생했습니다. 다시 시도해주세요.");
            }
        });
    } else {
        console.error("Nickname check button not found!");
    }

    // 전화번호 중복 확인 버튼 이벤트
    const checkPhoneButton = document.querySelector(".phone-group .check-btn");
    if (checkPhoneButton) {
        checkPhoneButton.addEventListener("click", async function () {
            const phone1 = "010";
            const phone2 = document.getElementById("phone2").value.trim();
            const phone3 = document.getElementById("phone3").value.trim();

            if (!phone2 || !phone3) {
                alert("전화번호를 모두 입력해주세요.");
                return;
            }

            const phoneNumber = `${phone1}${phone2}${phone3}`;

            try {
                const response = await fetch(`/service/checkphone?phone=${encodeURIComponent(phoneNumber)}`);
                const data = await response.json();

                if (response.ok) {
                    alert(data.message); // 중복 여부 메시지 출력
                } else {
                    alert(data.message || "중복 확인 중 오류가 발생했습니다.");
                }
            } catch (error) {
                console.error("Error during phone number check:", error);
                alert("중복 확인 중 문제가 발생했습니다. 다시 시도해주세요.");
            }
        });
    } else {
        console.error("Phone check button not found!");
    }

    // Error messages initially hidden
    document.querySelectorAll(".error-msg").forEach(function (element) {
        element.style.display = "none";
    });

    // Domain select change event listener
    document.getElementById('domain-select').addEventListener('change', function () {
        const customDomainInput = document.getElementById('custom-domain');
        if (this.value === 'custom') {
            customDomainInput.style.display = 'inline-block';
        } else {
            customDomainInput.style.display = 'none';
        }
    });

    // Form submission event listener
    document.getElementById('signup-form').addEventListener('submit', async function (event) {
        event.preventDefault(); // 기본 폼 제출 방지

        let hasError = false;

        // User ID validation
        const userId = document.getElementById("id").value.trim();
        if (userId === "") {
            document.getElementById("id-error").style.display = "block";
            hasError = true;
        } else {
            document.getElementById("id-error").style.display = "none";
        }

        // Password validation
        const password = document.getElementById("password").value.trim();
        if (password === "") {
            document.getElementById("password-error").style.display = "block";
            hasError = true;
        } else {
            document.getElementById("password-error").style.display = "none";
        }

        // Confirm Password validation
        const confirmPassword = document.getElementById("confirm-password").value.trim();
        if (confirmPassword !== password || confirmPassword === "") {
            document.getElementById("confirm-password-error").style.display = "block";
            hasError = true;
        } else {
            document.getElementById("confirm-password-error").style.display = "none";
        }

        // Nickname validation
        const nickname = document.getElementById("nickname").value.trim();
        if (nickname === "") {
            document.getElementById("nickname-error").style.display = "block";
            hasError = true;
        } else {
            document.getElementById("nickname-error").style.display = "none";
        }

        // Prevent form submission if there are errors
        if (hasError) {
            return;
        }

        // FormData 객체 생성
        const form = document.getElementById("signup-form");
        const formData = new FormData(form);

        try {
            // 서버로 데이터 전송
            const response = await fetch("/service/signup", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(errorData.message || "회원가입에 실패했습니다.");
                return;
            }

            alert("회원가입에 성공했습니다!");
            window.location.href = "/page/login";
        } catch (error) {
            console.error("Error during signup:", error);
            alert("회원가입 중 문제가 발생했습니다. 다시 시도해주세요.");
        }
    });
});