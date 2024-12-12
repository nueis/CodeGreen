// JWT 토큰을 로컬 스토리지에 저장
function storeJWT(token) {
    localStorage.setItem("auth_token", token);
}

async function fetchWithJWT(url, options = {}) {
  const token = localStorage.getItem("jwt"); // localStorage에서 JWT 가져오기

  if (!token) {
    throw new Error("JWT가 존재하지 않습니다. 로그인하세요.");
  }

  const headers = options.headers || {};
  headers["Authorization"] = `Bearer ${token}`; // Authorization 헤더에 JWT 추가

  // 옵션에 헤더를 병합
  options.headers = headers;

  // fetch 요청
  const response = await fetch(url, options);

  if (!response.ok) {
    if (response.status === 401) {
      alert("인증이 만료되었습니다. 다시 로그인해주세요.");
      localStorage.removeItem("jwt"); // JWT 삭제
      window.location.href = "/page/login"; // 로그인 페이지로 리다이렉트
    } else {
      const errorData = await response.json();
      throw new Error(errorData.message || "요청 실패");
    }
  }

  return await response.json();
}
