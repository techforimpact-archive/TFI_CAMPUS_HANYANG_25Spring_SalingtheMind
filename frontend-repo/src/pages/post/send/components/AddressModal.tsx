import Modal from '@/components/Modal';
import { useState } from 'react';
import styles from './addressmodal.module.css';
import { useUserStore } from '@/store/user';
import { useToastStore } from '@/store/toast';
import { LoadingSpinner } from '@/components/LoadingSpinner';

interface AddressModalProps {
  onSend: (address: string) => void;
  onClose: () => void;
  isLoading: boolean;
}

export default function AddressModal({ onSend, onClose, isLoading }: AddressModalProps) {
  const { userInfo, updateUserInfo, fetchUserInfo } = useUserStore();
  const { showToast } = useToastStore();
  const [address, setAddress] = useState(userInfo.address || '');
  const [isLoadingAddress, setIsLoading] = useState(isLoading);

  const handleSend = () => {
    if (!address.trim()) {
      showToast('주소를 입력해 주세요.');
      return;
    }

    setIsLoading(true);
    updateUserInfo({ ...userInfo, address })
      .then(() => {
        fetchUserInfo();
      })
      .finally(() => {
        setIsLoading(false);
        onSend(address);
      });
  };

  return (
    <Modal
      onClose={onClose}
      contentStyles={{
        backgroundColor: 'var(--orange-base-color)',
        width: '60%',
      }}
    >
      <div className={styles.container}>
        <img src="/image/post/otter_letter_love.webp" alt="온달" className={styles.otterImage} />
        <h2 className={styles.title}>📬이 편지의 손편지 답장을{'\n'}어디로 보내드릴까요?</h2>
        <p className={styles.description}>
          4주 이내로 온기우체부가 마음을 담아 보내드려요.{'\n'}잘 전달될 수 있도록 주소를
          확인해주세요!
        </p>
        <input
          type="text"
          value={address}
          onChange={e => setAddress(e.target.value)}
          placeholder="주소를 입력하세요"
          className={styles.input}
        />
        <button onClick={handleSend} className={styles.sendButton} disabled={isLoading}>
          {isLoading || isLoadingAddress ? (
            <LoadingSpinner spinnerSize={2} />
          ) : (
            <>
              <img src="/image/post/star.webp" alt="별" className={styles.starImage} />
              전송하기
            </>
          )}
        </button>
      </div>
    </Modal>
  );
}
