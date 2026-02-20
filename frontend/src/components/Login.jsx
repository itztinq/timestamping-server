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
            const response = await api.post('/auth/token', formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            localStorage.setItem('token', response.data.access_token);

            // Добиј ги податоците за корисникот за да ја зачуваме улогата
            const userResponse = await api.get('/auth/me');
            localStorage.setItem('role', userResponse.data.role);
            localStorage.setItem('username', userResponse.data.username);

            navigate('/dashboard');
        } catch (err) {
            console.error('Грешка при најава:', err);
            if (err.code === 'ERR_NETWORK') {
                setError('Нема врска со серверот. Проверете дали backend-от работи');
            } else if (err.response) {
                if (err.response.status === 401) {
                    setError('Грешно корисничко име или лозинка');
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