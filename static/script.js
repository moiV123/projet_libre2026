document.addEventListener('DOMContentLoaded', function () {

    const form = document.querySelector('form');

    if (!form) return;

    const champNom = document.querySelector('input[name="username"]');
    const champMotDePasse = document.querySelector('input[name="password"]');
    const champConfirmationMotDePasse =
        document.querySelector('input[name="confirm_password"]');

    const overlay = document.getElementById('loading-overlay');

    function validerChamp(champ, condition, message) {

        let erreur =
            champ.parentElement.querySelector('.message-erreur');

        if (!condition) {

            if (!erreur) {

                erreur = document.createElement('p');
                erreur.classList.add('message-erreur');

                champ.parentElement.appendChild(erreur);
            }

            erreur.textContent = message;

            champ.classList.add('champ-invalide');

            return false;

        } else {

            if (erreur) {
                erreur.remove();
            }

            champ.classList.remove('champ-invalide');

            return true;
        }
    }

    if (champNom) {
        champNom.addEventListener('input', function () {

            validerChamp(
                champNom,
                champNom.value.trim().length >= 3,
                "Le nom d'utilisateur doit comporter au moins 3 caractères."
            );

        });
    }

    if (champMotDePasse) {
        champMotDePasse.addEventListener('input', function () {

            validerChamp(
                champMotDePasse,
                champMotDePasse.value.trim().length >= 6,
                "Le mot de passe doit comporter au moins 6 caractères."
            );

        });
    }

    if (champConfirmationMotDePasse) {
        champConfirmationMotDePasse.addEventListener('input', function () {

            validerChamp(
                champConfirmationMotDePasse,
                champConfirmationMotDePasse.value === champMotDePasse.value,
                "Les mots de passe ne correspondent pas."
            );

        });
    }

    form.addEventListener('submit', function (event) {

        let nomOk = true;
        let motDePasseOk = true;
        let confirmationOk = true;

        if (champNom) {
            nomOk = validerChamp(
                champNom,
                champNom.value.trim().length >= 3,
                "Le nom d'utilisateur doit comporter au moins 3 caractères."
            );
        }

        if (champMotDePasse) {
            motDePasseOk = validerChamp(
                champMotDePasse,
                champMotDePasse.value.trim().length >= 6,
                "Le mot de passe doit comporter au moins 6 caractères."
            );
        }

        if (champConfirmationMotDePasse) {
            confirmationOk = validerChamp(
                champConfirmationMotDePasse,
                champConfirmationMotDePasse.value === champMotDePasse.value,
                "Les mots de passe ne correspondent pas."
            );
        }

        if (!nomOk || !motDePasseOk || !confirmationOk) {

            event.preventDefault();
            return;
        }

        if (overlay) {

            overlay.classList.remove('hidden');

            event.preventDefault();

            setTimeout(() => {
                form.submit();
            }, 1000);
        }
    });
});