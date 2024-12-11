document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault(); // 기본 폼 제출 동작 방지

  const id = document.getElementById("user-id").value;
  const password = document.getElementById("password").value;

  try {
    // 서버로 POST 요청
    const response = await fetch("/service/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ id, password }) // 서버로 ID와 비밀번호 전달
    });

    if (!response.ok) {
      const errorData = await response.json();
      alert(errorData.message || "로그인에 실패했습니다.");
      return;
    }

    const data = await response.json();
    const token = data.token;

    // JWT 저장
    localStorage.setItem("jwt", token);

    // 로그인 성공 시 home.html로 리다이렉트
    window.location.href = "/";
  } catch (error) {
    console.error("Error during login:", error);
    alert("아이디와 비밀번호를 올바르게 입력해주세요.");
  }
});