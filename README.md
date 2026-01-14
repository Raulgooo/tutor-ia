# TUTOR DE IA
 **Para este proyecto he decidido utilizar un flujo de agente de IA de 3 nodos en LangGraph para asegurarme de que el usuario no pueda violar bajo ninguna o casi ninguna circunstancia las restricciones de respuesta del modelo.**

 **La primera solucion que considere para el agente fue solo un System Prompt robusto para que el programa rechace siempre los intentos de trampa, pero no me convencio ya que es muy probable que el sistema en algun momento pueda caer en prompt injection. Mi segunda opcion fue utilizar langchain y otorgarle al agente una herramienta de checkeo de trampas pero igualmente me di cuenta que caia en lo mismo, el agente podia llegar a elegir no usar la herramienta en algun punto y para disminuir la superficie de errores se me ocurrio implementar un nodo Anti-Trampa inicial que se encarga de revisar la entrada del usuario justo antes de empezar a pensar en una respuesta, si determina que hay intenciones de trampa, el agente elige no proseguir con la peticion, el prompt se pasa al nodo de tutor y despues es revisado por un nodo guardian que verifica que no se haya violado la seguridad del primer nodo. De esta forma + system prompt bien planeado en el nodo de profesor llegamos a un metodo mas fiable para evitar trampas del usuario. Soy consciente de que esto puede añadir algo de overhead tecnico pero me parece necesario para hacer el sistema fiable, ademas el uso de langgraph me permite implementar un agente que es mas sencillo de controlar y que puede otorgar respuestas mejor curadas.**
 **Despues me parecio que seria util incluir memoria a corto plazo en el agente, para peticiones posteriores. Para acotar la implementacion me decidi por una memoria corta de 15 mensajes, de esta forma el agente puede responder dudas, revisarse a el mismo, y ofrecer ayuda extra al usuario sobre su tarea.**
 **Otra cosa que quiero añadir es citas tipo google si en la respuesta la IA menciona algo de la rubrica la IA dara un anchor sacado directo de la rubrica.**"

 ```mermaid
graph TD
    %% Nodos principales
    Start((Inicio)) --> PreAnalysis[Pre-Análisis]
    
    %% Decisiones del Nodo de Pre-Análisis
    PreAnalysis -.->|is_cheat / high_risk| NegativeFeedback[Feedback Negativo]
    PreAnalysis -.->|is_safe| Tutor[Tutor IA]
    
    %% Proceso de Tutoría
    Tutor --> PostAnalysis[Post-Análisis]
    
    %% Decisiones del Nodo de Post-Análisis
    PostAnalysis -.->|valid_output| End((Fin))
    PostAnalysis -.->|invalid_output| NegativeFeedback
    
    %% Salida final de error
    NegativeFeedback --> End

    %% Estilizado para que se vea Pro
    style Start fill:#f9f9f9,stroke:#333,stroke-width:2px
    style End fill:#bfb6fc,stroke:#333,stroke-width:4px
    style PreAnalysis fill:#e1f5fe,stroke:#01579b
    style Tutor fill:#e8f5e9,stroke:#2e7d32
    style PostAnalysis fill:#fff3e0,stroke:#ef6c00
    style NegativeFeedback fill:#ffebee,stroke:#c62828
```
