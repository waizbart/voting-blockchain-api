// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 *  Votações simples – cada transação representa 1 voto.
 *  • pollId     → identificador da enquete
 *  • option     → número / string curta da opção escolhida
 *  • voter      → endereço do remetente (útil para auditoria)
 *  Todos os votos são apenas logs (eventos). Não há storage,
 *  então o custo de gas é muito baixo (~ 22–25 k gas por voto).
 */
contract SimpleVoting {

    event Voted(
        uint256 indexed pollId,
        string  option,
        address indexed voter,
        uint256 timestamp
    );

    function vote(uint256 pollId, string calldata option) external {
        emit Voted(pollId, option, msg.sender, block.timestamp);
    }
}
