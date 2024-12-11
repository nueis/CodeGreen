// // JWT 토큰을 로컬 스토리지에 저장
// function storeJWT(token) {
//     localStorage.setItem("auth_token", token);
// }

// API 호출 시 JWT 토큰 사용 예시
function fetchWithJWT(url) {
    const token = localStorage.getItem("auth_token");

    if (token) {
        fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token  // 요청 헤더에 JWT 토큰 포함
            }
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
    } else {
        console.error("JWT token not found");
    }
}