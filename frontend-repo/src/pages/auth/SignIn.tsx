import { useAuthStore } from '@/store/auth';
import { Link, useNavigate } from 'react-router-dom';
import styles from './auth.module.css';
import ReactGA from 'react-ga4';
import { login } from '@/lib/api/user';
import { isErrorResponse } from '@/lib/response_dto';
import { useState } from 'react';
import { useToastStore } from '@/store/toast';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { useUserStore } from '@/store/user';
import { usePointStore } from '@/store/point';
import { useLetterStore } from '@/store/letter';
import { useItemStore } from '@/store/item';

export default function SignInPage() {
  const navigate = useNavigate();
  const { setLogin } = useAuthStore();
  const [nickname, setNickname] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { showToast } = useToastStore();

  const { fetchUserInfo } = useUserStore();
  const { fetchPoint } = usePointStore();
  const { fetchSavedLetters } = useLetterStore();
  const { fetchItems } = useItemStore();

  const handleLogin = async () => {
    console.log('로그인 버튼 클릭');

    if (!nickname) {
      showToast('닉네임을 입력해주세요.');
      return;
    }

    setIsLoading(true);

    const response = await login({ nickname });

    if (!response) {
      showToast('알 수 없는 오류가 발생했습니다.');
      setIsLoading(false);
      return;
    }

    if (isErrorResponse(response)) {
      showToast(response.error);
      setIsLoading(false);
      return;
    }

    showToast(response.message);
    setIsLoading(false);
    setLogin();

    // 조회 API 호출
    Promise.all([fetchPoint(), fetchUserInfo(), fetchSavedLetters(), fetchItems()]);

    ReactGA.set({ user_id: response.nickname });
    navigate('/', { replace: true });
  };

  return (
    <div className={styles.container}>
      <h1>마음의 항해</h1>
      <img
        className={styles.logoImage}
        src="image/login_setting/login_otter.webp"
        object-fit="cover"
        alt=""
      />
      <div className={styles.formContainer}>
        <div className={styles.labelContainer}>
          <label className={styles.label}>닉네임(ID)</label>
          <input
            className={styles.input}
            type="text"
            placeholder="닉네임(ID)"
            value={nickname}
            onChange={e => setNickname(e.target.value)}
            disabled={isLoading}
          />
        </div>
        <button className={styles.loginButton} onClick={handleLogin} disabled={isLoading}>
          {isLoading ? <LoadingSpinner spinnerSize={2} /> : '로그인 하기'}
        </button>
      </div>
      <Link to="/signup" className={styles.link}>
        회원가입
      </Link>
    </div>
  );
}
