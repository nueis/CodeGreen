document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault(); // 기본 폼 제출 동작 방지

  const id = document.getElementById("user-id").value;
  const password = document.getElementById("password").value;

  try {
    // 서버로 POST 요청
    const response = await fetch("/login", {
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

    // 홈 페이지로 리디렉션
    window.location.href = "/home";
  } catch (error) {
    console.error("Error during login:", error);
    alert("로그인 중 오류가 발생했습니다.");
  }
});