import { useState } from 'react';
import { Form, Button, Container, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import api from '../api/axiosConfig';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      // 2FA: сега користиме /auth/login наместо /auth/token
      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const data = response.data;

      if (data.requires_2fa) {
        // 2FA: потребно е да внесеме код
        // Го пренасочуваме кон /verify-otp со temp_token и mode='login'
        navigate('/verify-otp', { state: { tempToken: data.temp_token, mode: 'login' } });
      } else {
        // Ова не би требало да се случи бидејќи 2FA е задолжително, но оставаме за безбедност
        localStorage.setItem('token', data.access_token);
        const userResponse = await api.get('/auth/me');
        localStorage.setItem('role', userResponse.data.role);
        localStorage.setItem('username', userResponse.data.username);
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Грешка при најава:', err);
      if (err.code === 'ERR_NETWORK') {
        setError('Нема врска со серверот. Проверете дали backend-от работи');
      } else if (err.response) {
        if (err.response.status === 401) {
          setError('Грешно корисничко име или лозинка');
        } else if (err.response.status === 403) {
          setError('Профилот не е верификуван. Проверете ја вашата е-пошта.');
        } else if (err.response.status === 422) {
          setError('Невалидни податоци (проверете го форматот)');
        } else {
          setError(`Серверот врати грешка: ${err.response.status}`);
        }
      } else if (err.request) {
        setError('Нема одговор од серверот. Проверете дали backend-от работи.');
      } else {
        setError('Настана грешка: ' + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="mt-5" style={{ maxWidth: '400px' }}>
      <h2>Најава</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Корисничко име</Form.Label>
          <Form.Control
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Лозинка</Form.Label>
          <Form.Control
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </Form.Group>
        <Button variant="primary" type="submit" disabled={loading}>
          {loading ? 'Вчитување...' : 'Најави се'}
        </Button>
      </Form>
    </Container>
  );
}

export default Login;