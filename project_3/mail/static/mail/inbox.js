document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  document.querySelector("#compose-form").addEventListener("submit", send_mail)

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'block';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  fetch(`/emails/${mailbox}`)
.then(response => response.json())
.then(emails => {
  console.log(emails);

  emails.forEach(email => {
      console.log(email);

      const mail = document.createElement("div")
      mail.className = "email-strip"
      mail.id = email.read ? "read" : "unread"
      mail.innerHTML = `
        <div class="sender">${email.sender}</div>
        <div class="subject">${email.subject}</div>
        <div class="timestamp">${email.timestamp}</div>
      `
      mail.addEventListener("click", () => show_mail(email.id, mailbox))

      // Adding the new mail to the main DOM
      document.querySelector("#emails-view").append(mail)

    });

    // ... do something else with emails ...
});

}

function send_mail(event) {
  event.preventDefault()
  // Getting the variables from the html
  const recipients = document.querySelector("#compose-recipients").value
  const subject = document.querySelector("#compose-subject").value
  const body = document.querySelector("#compose-body").value

  // Sending the email with the API
  fetch('/emails', {
  method: 'POST',
  body: JSON.stringify({
    recipients: recipients,
    subject: subject,
    body: body
    })
  }).then(response => response.json())
  .then(result => {
  // Printing the result and going to "sent" tab
  console.log(result);
  load_mailbox("sent")
});

}

function show_mail(email_id, mailbox) {
  console.log(`you should have gone to the email with id: ${email_id}`)

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email);
      document.querySelector("#sender").textContent = `From: ${email.sender}`
      document.querySelector("#recipients").textContent = `To: ${email.recipients}`
      document.querySelector("#subject").textContent = `Subject: ${email.subject}`
      document.querySelector("#timestamp").textContent = `Timestamp: ${email.timestamp}`
      document.querySelector("#body").innerHTML = email.body.replace(/\n/g, "<br>");


      document.querySelector("#reply_btn").onclick = () => {
        compose_email()
        document.querySelector('#compose-recipients').value = `${email.sender}`
        document.querySelector('#compose-subject').value = email.subject.startsWith("Re:") ? `${email.subject}` : `Re: ${email.subject}`
        document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:\n${email.body}`

      }

      fetch(`/emails/${email_id}`, {
        method: "PUT",
        body: JSON.stringify({
          read: true
        })
      })


      const archive_btn = document.querySelector("#archive_btn");
      archive_btn.style.display = mailbox === "sent" ? "none" : "block"
      archive_btn.innerHTML = email.archived ? "Unarchive" : "Archive";
      archive_btn.onclick = () => {

      fetch(`/emails/${email_id}`, {
        method: "PUT",
        body: JSON.stringify({
          archived: !email.archived
        })
      })
      .then(() => load_mailbox("inbox"))

    }


});

}







