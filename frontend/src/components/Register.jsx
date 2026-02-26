import { useState } from 'react';
import { Form, Button, Container, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import api from '../api/axiosConfig';

function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');               // <-- 2FA: додадено поле за email
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validatePassword = (pass) => {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[-@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$/;
    return regex.test(pass);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Лозинките не се совпаѓаат');
      return;
    }

    if (!validatePassword(password)) {
      setError('Лозинката мора да има најмалку 8 знаци, голема буква, мала буква, број и специјален знак (-@$!%*?&_)');
      return;
    }

    setLoading(true);
    try {
      // 2FA: испраќаме и email
      const response = await api.post('/auth/register', {
        username,
        email,
        password,
      });

      // response.data содржи { message, temp_token }
      const { temp_token } = response.data;

      // Пренасочување кон страницата за внес на OTP, праќајќи го temp_token и mode='register'
      navigate('/verify-otp', { state: { tempToken: temp_token, mode: 'register' } });
    } catch (err) {
      setError(err.response?.data?.detail || 'Грешка при регистрација');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="mt-5" style={{ maxWidth: '400px' }}>
      <h2>Регистрација</h2>
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

        {/* 2FA: ново поле за email */}
        <Form.Group className="mb-3">
          <Form.Label>Е-пошта</Form.Label>
          <Form.Control
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="example@domain.com"
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
        <Form.Group className="mb-3">
          <Form.Label>Потврди лозинка</Form.Label>
          <Form.Control
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </Form.Group>
        <Button variant="primary" type="submit" disabled={loading}>
          {loading ? 'Регистрирање...' : 'Регистрирај се'}
        </Button>
      </Form>
    </Container>
  );
}

export default Register;