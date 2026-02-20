import { useState, useEffect } from 'react';
import { Container, Table, Button, Alert } from 'react-bootstrap';
import api from '../api/axiosConfig';

function Timestamps({ all = false }) {
    const [timestamps, setTimestamps] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [deleting, setDeleting] = useState(false);

    useEffect(() => {
        fetchTimestamps();
    }, []);

    const fetchTimestamps = async () => {
        try {
            const response = await api.get('/api/timestamps/');
            setTimestamps(response.data);
        } catch (err) {
            console.error('Грешка при вчитување:', err);
            setError('Грешка при вчитување на податоци');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Дали сте сигурни дека сакате да го избришете овој запис?')) return;
        setDeleting(true);
        try {
            await api.delete(`/api/timestamps/${id}`);
            setTimestamps(timestamps.filter(ts => ts.id !== id));
        } catch (err) {
            console.error('Грешка при бришење:', err);
            alert('Грешка при бришење');
        } finally {
            setDeleting(false);
        }
    };

    if (loading) return <Container className="mt-4">Вчитување...</Container>;
    if (error) return <Container className="mt-4"><Alert variant="danger">{error}</Alert></Container>;

    return (
        <Container className="mt-4">
            <h2>{all ? 'Сите записи' : 'Мои записи'}</h2>
            {timestamps.length === 0 ? (
                <Alert variant="info">Нема записи.</Alert>
            ) : (
                <Table striped bordered hover responsive>
                    <thead>
                    <tr>
                        <th>ID</th>
                        <th>Име на датотека</th>
                        <th>Хаш</th>
                        <th>Датум</th>
                        {all && <th>Корисник</th>}
                        <th>Акции</th>
                    </tr>
                    </thead>
                    <tbody>
                    {timestamps.map(ts => (
                        <tr key={ts.id}>
                            <td>{ts.id}</td>
                            <td>{ts.filename}</td>
                            <td style={{ wordBreak: 'break-all' }}>{ts.file_hash}</td>
                            <td>{new Date(ts.timestamp).toLocaleString()}</td>
                            {all && <td>{ts.username || ts.user_id}</td>}
                            <td>
                                <Button
                                    variant="danger"
                                    size="sm"
                                    onClick={() => handleDelete(ts.id)}
                                    disabled={deleting}
                                >
                                    Избриши
                                </Button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </Table>
            )}
        </Container>
    );
}

export default Timestamps;