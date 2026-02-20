import { useState, useEffect } from 'react';
import { Container, Card, Alert, Button } from 'react-bootstrap';
import api from '../api/axiosConfig';

function Certificate() {
    const [cert, setCert] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchCert = async () => {
            try {
                const response = await api.get('/api/timestamps/cert');
                setCert(response.data.certificate);
            } catch (err) {
                console.error(err);
                setError('Грешка при вчитување на сертификат');
            } finally {
                setLoading(false);
            }
        };
        fetchCert();
    }, []);

    const copyToClipboard = () => {
        navigator.clipboard.writeText(cert);
        alert('Сертификатот е копиран во клипборд');
    };

    if (loading) return <Container>Вчитување...</Container>;
    if (error) return <Container><Alert variant="danger">{error}</Alert></Container>;

    return (
        <Container className="mt-4">
            <h2>Сертификат на серверот</h2>
            <Card>
                <Card.Body>
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
            {cert}
          </pre>
                </Card.Body>
                <Card.Footer>
                    <Button variant="secondary" onClick={copyToClipboard}>
                        Копирај сертификат
                    </Button>
                </Card.Footer>
            </Card>
        </Container>
    );
}

export default Certificate;