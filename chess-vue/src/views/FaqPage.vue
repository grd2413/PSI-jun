<template>
  <h1>FAQ</h1>

  <div class="row">
    <div class="accordion col-12" id="accordionFaq">
      <!--Item 1-->
      <div class="accordion-item">
        <!--Item 1 header-->
        <h2 class="accordion-header">
          <button
            class="accordion-button"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#collapse1"
            aria-expanded="true"
            aria-controls="collapse1"
          >
            How can players update the result of a game?
          </button>
        </h2>

        <!--Item 1 text-->
        <div
          id="collapse1"
          class="accordion-collapse collapse show"
          data-bs-parent="#accordionFaq"
          style=""
        >
          <div class="accordion-body">
            Go to the tournament page, open the "pairing/results" tab, provide
            de lichess game id in the input field (for lichess games) or select
            the result from the dropdown list (for OTB games) and then click on
            the
            <i class="bi bi-send"></i> icon.
          </div>
        </div>
      </div>
      <!--Item 2-->
      <div class="accordion-item">
        <!--Item 2 header-->
        <h2 class="accordion-header">
          <button
            class="accordion-button"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#collapse2"
            aria-expanded="true"
            aria-controls="collapse2"
          >
            How can administrators add players to a tournament?
          </button>
        </h2>

        <!--Item 1 text-->
        <div
          id="collapse2"
          class="accordion-collapse collapse show"
          data-bs-parent="#accordionFaq"
          style=""
        >
          <div class="accordion-body">
            <p>
              Players are added using the CSV file format. Comma-separated
              values (CSV) is a text format that uses commas to separate values,
              and newlines to separate records. The first row of the CSV file
              must contain the column names.
            </p>
            <p>
              The column names must match the fields of the player. The more
              common fields are: <i>name</i>, <i>email</i>,
              <i>lichess_username</i>.
            </p>
            <p>
              For lichess tournaments, the <i>lichess_username</i> is required.
              For OTB tournaments, the <i>name</i> and <i>email</i> are
              required.
            </p>
            <p>
              For lichess tournaments, the <i>lichess_username</i> will be
              checked again lichess database and the player ranking will be
              retrieved. For OTB tournaments, the <i>email</i> will be used as
              user password.
            </p>
            <p>
              example lichess tournament<br /><code>
                lichess_username<br />
                username1<br />
                username2<br />
                username3<br
              /></code>
            </p>
            <p>
              example OTB tournament<br /><code>
                name, email<br />
                name1 familyname1, name1@gmail.com<br />
                name2 familyname2, name2@gmail.com<br />
                name3 familyname3, name3@gmail.com<br
              /></code>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.accordion-item:first-child .accordion-button {
  border-top-left-radius: var(--bs-accordion-inner-border-radius) !important;
  border-top-right-radius: var(--bs-accordion-inner-border-radius) !important;
}

.accordion-item:last-child .accordion-button.collapsed {
  border-bottom-left-radius: var(--bs-accordion-inner-border-radius) !important;
  border-bottom-right-radius: var(
    --bs-accordion-inner-border-radius
  ) !important;
}

.accordion-item:not(:first-child):not(:last-child) .accordion-button {
  border-radius: 0 !important;
}
</style>
