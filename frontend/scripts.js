let dadosCasos = [];

async function carregarDados() {
    try {
        const res = await fetch('https://localhost: 5000/api/casos');
        dadosCasos = await res.json();
        console.log("Dados carregados:", dadosCasos);
        atualizarGraficos();
        } catch (error) {
        console.error("Erro ao carregar os dados:", error);
        alert("Erro ao carregar os dados. Verifique o console para mais detalhes.");
    }
}

function filtrarPorData(casos) {
    const fim = document.getElementById('dataFim').value;
    
    return casos.filter(caso => {
        if (!caso.data_do_caso) return false;
        const data = new Date(caso.data_do_caso);
        const dataInicio = inicio ? new Date(inicio) : null;
        const dataFim = fim ? new Date(fim) : null;
        return (!dataInicio || data >= dataInicio) && (!dataFim || data <= dataFim);
    }
    );
}

function atualizarGraficos() {
    const dadosFiltrados = filtrarPorData(dadosCasos);
    console.log("Dados filtrados:", dadosFiltrados);
    if (dadosFiltrados.length === 0) {
        alert("Nenhum caso encontrado para o período selecionado.");
        return;
    }
}

document.getElementById('dataFim').addEventListener('change', atualizarGraficos);
document.getElementById('dataInicio').addEventListener('change', atualizarGraficos);

carregarDados();