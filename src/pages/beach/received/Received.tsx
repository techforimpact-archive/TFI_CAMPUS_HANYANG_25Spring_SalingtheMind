import Appbar from '@/components/Appbar';
import styles from '../../post/received.module.css';
import { useNavigate } from 'react-router-dom';
export default function ReceivedPage() {
  const navigate = useNavigate();

  return (
    <>

      <div className={styles.container}>
      <Appbar title="" />
        <div className={styles.speechBubble}>
          <div className={styles.bubbleText}>
            <h4>OO 님,{'\n'}어떤 이야기를 들어보실래요?</h4>
          </div>
        </div>

        <div className="nav-button-container">
          <button onClick={() => navigate('/received/letters')}>
            <img src="/image/common/paper_boat.webp" object-fit="cover" alt="letter" />
            흘러온 편지
          </button>
          <button onClick={() => navigate('/received/responses')}>
            <img src="/image/beach/bottle.webp" alt="storage" />
            받은 답장
          </button>
        </div>
      </div>
    </>
  );
}
