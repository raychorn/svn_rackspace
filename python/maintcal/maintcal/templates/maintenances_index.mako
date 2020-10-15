<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
  <head>
    <title>${c.title}</title>
  </head>
  <body>
    <table>
        <tr><th>ID</th><th>Ticket</th><th>Description</th></tr>
        % for maint in c.maints:
        <tr>
            <td><a href=${h.url_for(controller='maintenances', action='show', id=maint.id)}>${maint.id}</a></td>
            <td>${maint.master_ticket}</td>
            <td>${maint.general_description}</td>
        </tr>
        % endfor
    </table>
  </body>
</html>
