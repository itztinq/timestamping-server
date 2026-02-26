import { useState } from 'react';
import { Container, Form, Button, Alert, Card } from 'react-bootstrap';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../api/axiosConfig';

function VerifyOTP() {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Очекуваме дека при пренасочување кон оваа страница праќаме state:
  // - tempToken: привремениот токен
  // - mode: 'register' или 'login'
  const { tempToken, mode } = location.state || {};

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Одреди го ендпоинтот според mode-от
    const endpoint = mode === 'register' ? '/auth/verify-otp' : '/auth/verify-login';

    try {
      const response = await api.post(
        endpoint,
        { code },
        {
          headers: {
            'X-Temp-Token': tempToken,   // го праќаме tempToken во header
          },
        }
      );

      // По успешна верификација, го добиваме вистинскиот access_token
      localStorage.setItem('token', response.data.access_token);

      // Преземаме податоци за корисникот
      const userResponse = await api.get('/auth/me');
      localStorage.setItem('role', userResponse.data.role);
      localStorage.setItem('username', userResponse.data.username);

      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Грешка при верификација на кодот');
    } finally {
      setLoading(false);
    }
  };

  if (!tempToken) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">Недостасува привремен токен. Вратете се на почеток.</Alert>
      </Container>
    );
  }

  return (
    <Container className="mt-5" style={{ maxWidth: '400px' }}>
      <h2>Верификација на код</h2>
      <p>Внесете го шестцифрениот код што го добивте на вашата е-пошта.</p>
      {error && <Alert variant="danger">{error}</Alert>}
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Код</Form.Label>
          <Form.Control
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            maxLength={6}
            required
            placeholder="000000"
          />
        </Form.Group>
        <Button variant="primary" type="submit" disabled={loading}>
          {loading ? 'Верификација...' : 'Верифицирај'}
        </Button>
      </Form>
    </Container>
  );
}

export default VerifyOTP;